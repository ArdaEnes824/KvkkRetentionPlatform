using System;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KvkkRetentionPlatform.Models.Entities;

namespace KvkkRetentionPlatform.Controllers
{
    public class DashboardController : Controller
    {
        private readonly KvkkDbContext _context;

        public DashboardController(KvkkDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var totalActiveData = await _context.PersonalDataEntries
                .CountAsync(x => x.Status == "ACTIVE");

            var expiredDataList = await _context.VwExpiredDataForActions.ToListAsync();
            var dataPendingDeletion = expiredDataList.Count;

            // Chart 1: Categories
            var categoryStats = await _context.PersonalDataEntries
                .Include(p => p.Category)
                .Where(p => p.Status == "ACTIVE")
                .GroupBy(p => p.Category.CategoryName)
                .Select(g => new { Category = g.Key, Count = g.Count() })
                .ToListAsync();

            // Chart 2: Expirations (Next upcoming 12 months with expirations)
            var expirationStats = await _context.PersonalDataEntries
                .Where(p => p.Status == "ACTIVE" && p.ExpirationDate.HasValue)
                .GroupBy(p => new { p.ExpirationDate.Value.Year, p.ExpirationDate.Value.Month })
                .Select(g => new { Year = g.Key.Year, Month = g.Key.Month, Count = g.Count() })
                .OrderBy(g => g.Year).ThenBy(g => g.Month)
                .Take(12)
                .ToListAsync();

            var model = new DashboardViewModel
            {
                TotalActiveData = totalActiveData,
                DataPendingDeletion = dataPendingDeletion,
                ExpiredDataList = expiredDataList,
                CategoryLabels = categoryStats.Select(x => x.Category).ToList(),
                CategoryCounts = categoryStats.Select(x => x.Count).ToList(),
                ExpirationLabels = expirationStats.Select(x => $"{x.Month:D2}/{x.Year}").ToList(),
                ExpirationCounts = expirationStats.Select(x => x.Count).ToList()
            };

            return View(model);
        }

        [HttpPost]
        public async Task<IActionResult> RunRetentionJob()
        {
            await _context.Database.ExecuteSqlRawAsync("EXEC sp_ProcessExpiredData");
            TempData["Message"] = "Retention job executed successfully. Expired data has been processed.";
            return RedirectToAction(nameof(Index));
        }

        [HttpPost]
        public async Task<IActionResult> ForceForgetSubject(string email, string reason)
        {
            if (string.IsNullOrWhiteSpace(email)) return RedirectToAction(nameof(Index));

            var subject = await _context.DataSubjects
                .Include(s => s.PersonalDataEntries)
                .FirstOrDefaultAsync(s => s.Email == email);

            if (subject != null && subject.PersonalDataEntries.Any())
            {
                foreach (var entry in subject.PersonalDataEntries)
                {
                    entry.DataValue = "ANONYMIZED_" + Guid.NewGuid().ToString().Substring(0, 8);
                    entry.Status = "ANONYMIZED";
                }
                
                string finalReason = string.IsNullOrWhiteSpace(reason) ? "Belirtilmedi" : reason;
                
                _context.AuditLogs.Add(new AuditLog
                {
                    TableName = "PersonalDataEntries",
                    RecordId = subject.Id,
                    Action = "UPDATE",
                    ActionDate = DateTime.Now,
                    PerformedBy = "System",
                    Details = $"Unutulma Hakkı: {email} kullanıcısına ait {subject.PersonalDataEntries.Count} adet veri '{finalReason}' nedeniyle silindi/anonimleştirildi."
                });

                await _context.SaveChangesAsync();
                TempData["Message"] = $"{email} için Unutulma Hakkı başarıyla uygulandı.";
            }
            else
            {
                TempData["Message"] = "Kullanıcı veya silinecek veri bulunamadı.";
            }

            return RedirectToAction(nameof(Index));
        }
    }

    public class DashboardViewModel
    {
        public int TotalActiveData { get; set; }
        public int DataPendingDeletion { get; set; }
        public List<VwExpiredDataForAction> ExpiredDataList { get; set; } = new List<VwExpiredDataForAction>();
        
        public List<string> CategoryLabels { get; set; } = new List<string>();
        public List<int> CategoryCounts { get; set; } = new List<int>();
        
        public List<string> ExpirationLabels { get; set; } = new List<string>();
        public List<int> ExpirationCounts { get; set; } = new List<int>();
    }
}
