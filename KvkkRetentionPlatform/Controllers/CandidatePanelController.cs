using System.Security.Claims;
using KvkkRetentionPlatform.Models;
using KvkkRetentionPlatform.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KvkkRetentionPlatform.Helpers;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;

namespace KvkkRetentionPlatform.Controllers
{
    [Authorize(Roles = "Candidate")]
    public class CandidatePanelController : Controller
    {
        private readonly KvkkDbContext _context;

        public CandidatePanelController(KvkkDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (string.IsNullOrEmpty(userIdStr) || !int.TryParse(userIdStr, out int userId))
            {
                return RedirectToAction("Login", "Auth");
            }

            var subject = await _context.DataSubjects
                .Include(s => s.PersonalDataEntries)
                .ThenInclude(p => p.Category)
                .Include(s => s.ConsentLogs)
                .FirstOrDefaultAsync(s => s.Id == userId);

            if (subject == null)
            {
                return RedirectToAction("Login", "Auth");
            }

            var tcknEntry = subject.PersonalDataEntries.FirstOrDefault(p => p.CategoryId == 1 && p.Status == "ACTIVE");
            var phoneEntry = subject.PersonalDataEntries.FirstOrDefault(p => p.CategoryId == 2 && p.Status == "ACTIVE");
            var consentLog = subject.ConsentLogs.OrderByDescending(c => c.ConsentDate).FirstOrDefault();

            var viewModel = new CandidatePanelViewModel
            {
                Subject = subject,
                MaskedTckn = tcknEntry != null ? DataMaskingHelper.MaskData(tcknEntry.DataValue) : "Bulunamadı",
                MaskedPhone = phoneEntry != null ? DataMaskingHelper.MaskData(phoneEntry.DataValue) : "Bulunamadı",
                IsConsentActive = consentLog != null && !consentLog.IsRevoked
            };

            return View(viewModel);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> UpdateProfile(string firstName, string lastName, string emailAddr, string phoneNumber, string education, string workExperience, IFormFile cvFile)
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");
            
            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == email);
            if (subject == null) return RedirectToAction("Login", "Auth");
            
            // Update Name and Surname
            if (!string.IsNullOrWhiteSpace(firstName)) subject.FirstName = firstName;
            if (!string.IsNullOrWhiteSpace(lastName)) subject.LastName = lastName;

            // Update Email
            if (!string.IsNullOrWhiteSpace(emailAddr) && emailAddr != subject.Email)
            {
                subject.Email = emailAddr;
            }

            // Update Phone via PersonalDataEntry (CategoryId = 2 indicates contact/phone data)
            if (!string.IsNullOrWhiteSpace(phoneNumber))
            {
                var existingPhoneEntry = await _context.PersonalDataEntries
                    .FirstOrDefaultAsync(d => d.SubjectId == subject.Id && d.CategoryId == 2 && d.Status == "ACTIVE");
                    
                if (existingPhoneEntry != null)
                {
                    existingPhoneEntry.DataValue = phoneNumber;
                    existingPhoneEntry.CollectedAt = DateTime.Now;
                }
                else
                {
                    _context.PersonalDataEntries.Add(new PersonalDataEntry {
                        SubjectId = subject.Id, CategoryId = 2, DataValue = phoneNumber, 
                        CollectedAt = DateTime.Now, ExpirationDate = DateTime.Now.AddYears(5), Status = "ACTIVE"
                    });
                }
            }

            if (!string.IsNullOrWhiteSpace(education))
            {
                _context.PersonalDataEntries.Add(new PersonalDataEntry {
                    SubjectId = subject.Id, CategoryId = 4, DataValue = education, 
                    CollectedAt = DateTime.Now, ExpirationDate = DateTime.Now.AddYears(10), Status = "ACTIVE"
                });
            }

            if (!string.IsNullOrWhiteSpace(workExperience))
            {
                _context.PersonalDataEntries.Add(new PersonalDataEntry {
                    SubjectId = subject.Id, CategoryId = 5, DataValue = workExperience, 
                    CollectedAt = DateTime.Now, ExpirationDate = DateTime.Now.AddYears(10), Status = "ACTIVE"
                });
            }

            if (cvFile != null && cvFile.Length > 0 && cvFile.FileName.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
            {
                var uploadDir = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "uploads", "cvs");
                if (!Directory.Exists(uploadDir)) Directory.CreateDirectory(uploadDir);
                
                var fileName = Guid.NewGuid().ToString() + ".pdf";
                var filePath = Path.Combine(uploadDir, fileName);
                
                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await cvFile.CopyToAsync(stream);
                }

                _context.PersonalDataEntries.Add(new PersonalDataEntry {
                    SubjectId = subject.Id, CategoryId = 3, DataValue = $"/uploads/cvs/{fileName}", 
                    CollectedAt = DateTime.Now, ExpirationDate = DateTime.Now.AddYears(5), Status = "ACTIVE"
                });
            }

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = "Profil bilgileriniz KVKK kurallarına uygun olarak başarıyla kaydedildi.";
            return RedirectToAction("Index");
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> DeleteMyAccount()
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");

            var subject = await _context.DataSubjects
                .Include(s => s.PersonalDataEntries)
                .Include(s => s.JobApplications)
                .FirstOrDefaultAsync(s => s.Email == email);

            if (subject != null)
            {
                // 1. Delete physical CV file
                var cvEntry = subject.PersonalDataEntries.FirstOrDefault(p => p.CategoryId == 3);
                if (cvEntry != null && !string.IsNullOrEmpty(cvEntry.DataValue))
                {
                    var filePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", cvEntry.DataValue.TrimStart('/').Replace('/', '\\'));
                    if (System.IO.File.Exists(filePath))
                    {
                        System.IO.File.Delete(filePath);
                        
                        _context.AuditLogs.Add(new AuditLog
                        {
                            TableName = "Files System",
                            RecordId = subject.Id,
                            Action = "DELETE",
                            ActionDate = DateTime.Now,
                            PerformedBy = "SelfService",
                            Details = $"Fiziksel Özgeçmiş (CV) dosyası sunucudan kalıcı olarak imha edildi: {cvEntry.DataValue}"
                        });
                    }
                }

                // 2. Remove Personal Data Entries completely
                _context.PersonalDataEntries.RemoveRange(subject.PersonalDataEntries);

                // 3. Optional: Cancel all active applications logic
                foreach (var app in subject.JobApplications)
                {
                    app.Status = "İptal Edildi";
                }

                // 4. Anonymize identity (User Soft Delete)
                var salt = Guid.NewGuid().ToString("N").Substring(0, 8);
                subject.FirstName = "Silinmiş";
                subject.LastName = "Kullanıcı";
                subject.Email = $"deleted_{salt}@anonymized.local";
                subject.Password = null;
                subject.ConsentIpAddress = null;
                subject.IsAnonymized = true;

                _context.AuditLogs.Add(new AuditLog
                {
                    TableName = "DataSubjects",
                    RecordId = subject.Id,
                    Action = "ANONYMIZE",
                    ActionDate = DateTime.Now,
                    PerformedBy = "SelfService",
                    Details = $"Aday kendi talebiyle KVKK Madde 11 (Unutulma Hakkı) kapsamında verilerini ve fiziksel dosyalarını sildi."
                });

                await _context.SaveChangesAsync();
            }

            // Logout and redirect
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            TempData["SuccessMessage"] = "KVKK kapsamındaki unutulma hakkınız gereği tüm dosyalarınız fiziksel olarak silinmiş ve hesabınız anonimleştirilmiştir.";
            return RedirectToAction("Index", "Home");
        }

        [HttpGet]
        public async Task<IActionResult> OpenJobs()
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");

            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == email);
            if (subject == null) return RedirectToAction("Login", "Auth");

            var appliedJobIds = await _context.JobApplications
                .Where(a => a.SubjectId == subject.Id && a.Status != "İptal Edildi")
                .Select(a => a.JobPostingId)
                .ToListAsync();

            var jobs = await _context.JobPostings
                .Where(j => j.Status == "Açık" && !appliedJobIds.Contains(j.Id))
                .OrderByDescending(j => j.CreatedAt)
                .ToListAsync();
                
            return View(jobs);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ApplyToJob(int jobId)
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");

            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == email);
            if (subject == null) return RedirectToAction("Login", "Auth");

            var existingApp = await _context.JobApplications
                .FirstOrDefaultAsync(a => a.SubjectId == subject.Id && a.JobPostingId == jobId);
                
            if (existingApp != null)
            {
                if (existingApp.Status != "İptal Edildi")
                {
                    TempData["ErrorMessage"] = "Bu ilana zaten aktif bir başvurunuz bulunuyor.";
                    return RedirectToAction("OpenJobs");
                }
                else
                {
                    existingApp.Status = "Bekleniyor";
                    existingApp.ApplicationDate = DateTime.Now;
                    await _context.SaveChangesAsync();
                    TempData["SuccessMessage"] = "İptal ettiğiniz başvurunuz başarıyla yenilendi!";
                    return RedirectToAction("MyApplications");
                }
            }

            var application = new JobApplication
            {
                SubjectId = subject.Id,
                JobPostingId = jobId,
                ApplicationDate = DateTime.Now,
                Status = "Bekleniyor"
            };

            _context.JobApplications.Add(application);
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = "Başvurunuz başarıyla alındı!";
            return RedirectToAction("MyApplications");
        }

        [HttpGet]
        public async Task<IActionResult> MyApplications()
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");

            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == email);
            if (subject == null) return RedirectToAction("Login", "Auth");

            var applications = await _context.JobApplications
                .Include(a => a.JobPosting)
                .Where(a => a.SubjectId == subject.Id)
                .OrderByDescending(a => a.ApplicationDate)
                .ToListAsync();

            return View(applications);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> CancelApplication(int id)
        {
            var email = User.FindFirstValue(ClaimTypes.Email);
            if (string.IsNullOrEmpty(email)) return RedirectToAction("Login", "Auth");

            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == email);
            if (subject == null) return RedirectToAction("Login", "Auth");

            var application = await _context.JobApplications
                .FirstOrDefaultAsync(a => a.Id == id && a.SubjectId == subject.Id);
                
            if (application != null && application.Status == "Bekleniyor")
            {
                application.Status = "İptal Edildi";
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Başvurunuz başarıyla iptal edildi.";
            }

            return RedirectToAction("MyApplications");
        }
    }
}
