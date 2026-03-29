using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KvkkRetentionPlatform.Models.Entities;
using System;
using System.Threading.Tasks;

namespace KvkkRetentionPlatform.Controllers
{
    public class ConsentsController : Controller
    {
        private readonly KvkkDbContext _context;

        public ConsentsController(KvkkDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var activeConsents = await _context.VwActiveConsentLogs.ToListAsync();
            return View(activeConsents);
        }

        [HttpPost]
        public async Task<IActionResult> RevokeConsent(int id)
        {
            var consent = await _context.ConsentLogs.FindAsync(id);
            if (consent != null)
            {
                consent.IsRevoked = true;
                consent.RevokedAt = DateTime.Now;
                
                _context.AuditLogs.Add(new AuditLog
                {
                    TableName = "ConsentLogs",
                    RecordId = consent.Id,
                    Action = "UPDATE",
                    ActionDate = DateTime.Now,
                    PerformedBy = "System",
                    Details = $"Rıza iptali: SubjectId: {consent.SubjectId}, CategoryId: {consent.CategoryId} rızası geri çekildi."
                });

                await _context.SaveChangesAsync();
                TempData["Message"] = "Kullanıcı rızası başarıyla geri çekildi.";
            }

            return RedirectToAction(nameof(Index));
        }
    }
}
