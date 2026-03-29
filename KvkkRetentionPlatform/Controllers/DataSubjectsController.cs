using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KvkkRetentionPlatform.Models.Entities;
using System.Linq;
using System.Threading.Tasks;

namespace KvkkRetentionPlatform.Controllers
{
    public class DataSubjectsController : Controller
    {
        private readonly KvkkDbContext _context;

        public DataSubjectsController(KvkkDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> Index(string sortOrder)
        {
            ViewData["CurrentSort"] = sortOrder;

            var subjectsQuery = _context.DataSubjects
                .Include(s => s.PersonalDataEntries)
                .ThenInclude(p => p.Category)
                .Include(s => s.JobApplications)
                .ThenInclude(a => a.JobPosting)
                .AsQueryable();

            switch (sortOrder)
            {
                case "name_asc":
                    subjectsQuery = subjectsQuery.OrderBy(s => s.FirstName).ThenBy(s => s.LastName);
                    break;
                case "name_desc":
                    subjectsQuery = subjectsQuery.OrderByDescending(s => s.FirstName).ThenByDescending(s => s.LastName);
                    break;
                case "date_asc":
                    subjectsQuery = subjectsQuery.OrderBy(s => s.CreatedAt);
                    break;
                case "date_desc":
                default:
                    subjectsQuery = subjectsQuery.OrderByDescending(s => s.CreatedAt);
                    break;
            }

            var subjects = await subjectsQuery.ToListAsync();

            var model = subjects.Select(s => new DataSubjectListViewModel
            {
                Id = s.Id,
                FullName = $"{s.FirstName} {s.LastName}",
                Email = s.Email,
                CreatedAt = s.CreatedAt,
                MaskedTckn = KvkkRetentionPlatform.Helpers.DataMaskingHelper.MaskData(s.PersonalDataEntries.FirstOrDefault(p => p.CategoryId == 1 && p.Status == "ACTIVE")?.DataValue ?? string.Empty),
                MaskedPhone = KvkkRetentionPlatform.Helpers.DataMaskingHelper.MaskData(s.PersonalDataEntries.FirstOrDefault(p => p.Status == "ACTIVE" && (p.Category.CategoryName.ToLower().Contains("telefon") || p.Category.CategoryName.ToLower().Contains("phone")))?.DataValue ?? string.Empty),
                Applications = s.JobApplications.OrderByDescending(a => a.ApplicationDate).Select(a => new UserJobAppDto {
                    JobTitle = a.JobPosting.Title,
                    ApplicationDate = a.ApplicationDate,
                    Status = a.Status
                }).ToList()
            }).ToList();

            return View(model);
        }

        [HttpGet]
        public async Task<IActionResult> ExportUserData(int? subjectId, string email)
        {
            DataSubject subject = null;
            
            var query = _context.DataSubjects
                .Include(s => s.PersonalDataEntries)
                .ThenInclude(p => p.Category)
                .Include(s => s.ConsentLogs)
                .ThenInclude(c => c.Category)
                .AsQueryable();

            if (subjectId.HasValue && subjectId.Value > 0)
                subject = await query.FirstOrDefaultAsync(s => s.Id == subjectId.Value);
            else if (!string.IsNullOrEmpty(email))
                subject = await query.FirstOrDefaultAsync(s => s.Email == email);

            if (subject == null)
                return NotFound("Kullanıcı bulunamadı.");

            var exportData = new
            {
                Subject = new { subject.FirstName, subject.LastName, subject.Email, subject.CreatedAt },
                PersonalData = subject.PersonalDataEntries.Select(p => new {
                    Category = p.Category.CategoryName,
                    Value = p.DataValue,
                    p.CollectedAt,
                    p.ExpirationDate,
                    p.Status
                }),
                Consents = subject.ConsentLogs.Select(c => new {
                    Category = c.Category.CategoryName,
                    c.ConsentDate,
                    c.IsRevoked,
                    c.RevokedAt
                })
            };

            var jsonBytes = System.Text.Json.JsonSerializer.SerializeToUtf8Bytes(exportData, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
            return File(jsonBytes, "application/json", $"UserData_{subject.Id}_{System.DateTime.Now:yyyyMMdd}.json");
        }

        [HttpGet]
        public IActionResult Create()
        {
            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(DataSubject subject, string tckn, string phoneNumber)
        {
            if (ModelState.IsValid)
            {
                subject.CreatedAt = System.DateTime.Now;
                _context.DataSubjects.Add(subject);
                
                // Add the DataSubject first to get its ID
                await _context.SaveChangesAsync();
                
                // Add TCKN as PersonalDataEntry if provided
                if (!string.IsNullOrWhiteSpace(tckn))
                {
                    var dataEntryTckn = new PersonalDataEntry
                    {
                        SubjectId = subject.Id,
                        CategoryId = 1, // Kimlik Verisi Kategorisi
                        DataValue = tckn,
                        CollectedAt = System.DateTime.Now,
                        ExpirationDate = System.DateTime.Now.AddYears(10), // Politikaya uygun süre
                        Status = "ACTIVE"
                    };
                    _context.PersonalDataEntries.Add(dataEntryTckn);
                }

                // Add Phone as PersonalDataEntry if provided
                if (!string.IsNullOrWhiteSpace(phoneNumber))
                {
                    var dataEntryPhone = new PersonalDataEntry
                    {
                        SubjectId = subject.Id,
                        CategoryId = 2, // İletişim Kategorisi
                        DataValue = phoneNumber,
                        CollectedAt = System.DateTime.Now,
                        ExpirationDate = System.DateTime.Now.AddYears(5), // İletişim politikası
                        Status = "ACTIVE"
                    };
                    _context.PersonalDataEntries.Add(dataEntryPhone);
                }

                _context.AuditLogs.Add(new AuditLog
                {
                    TableName = "DataSubjects",
                    RecordId = subject.Id,
                    Action = "INSERT",
                    ActionDate = System.DateTime.Now,
                    PerformedBy = "System",
                    Details = $"Yeni kullanıcı, TCKN ve Telefon verisi sisteme eklendi. Email: {subject.Email}"
                });

                await _context.SaveChangesAsync();
                TempData["Message"] = "Yeni ilgili kişi ve verileri başarıyla eklendi.";
                return RedirectToAction("Index", "Dashboard");
            }
            return View(subject);
        }
    }

    public class DataSubjectListViewModel
    {
        public int Id { get; set; }
        public string FullName { get; set; } = null!;
        public string Email { get; set; } = null!;
        public System.DateTime CreatedAt { get; set; }
        public string MaskedTckn { get; set; } = null!;
        public string MaskedPhone { get; set; } = null!;
        public List<UserJobAppDto> Applications { get; set; } = new List<UserJobAppDto>();
    }

    public class UserJobAppDto
    {
        public string JobTitle { get; set; } = null!;
        public System.DateTime ApplicationDate { get; set; }
        public string Status { get; set; } = null!;
    }
}
