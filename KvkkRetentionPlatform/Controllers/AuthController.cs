using System.Security.Claims;
using KvkkRetentionPlatform.Models;
using KvkkRetentionPlatform.Models.Entities;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace KvkkRetentionPlatform.Controllers
{
    public class AuthController : Controller
    {
        private readonly KvkkDbContext _context;

        public AuthController(KvkkDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> Login()
        {
            // Güçlü çıkış: Yeni loginden önce var olan oturumu süpür
            if (User.Identity != null && User.Identity.IsAuthenticated)
            {
                await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            }
            
            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Login(LoginViewModel model)
        {
            if (!ModelState.IsValid) return View(model);

            // Admin Check
            if (model.Email == "admin@admin.com" && model.Password == "admin")
            {
                var claims = new List<Claim>
                {
                    new Claim(ClaimTypes.Name, "Admin"),
                    new Claim(ClaimTypes.Email, model.Email),
                    new Claim(ClaimTypes.Role, "Admin")
                };

                var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                var authProperties = new AuthenticationProperties { IsPersistent = model.RememberMe };

                await HttpContext.SignInAsync(
                    CookieAuthenticationDefaults.AuthenticationScheme,
                    new ClaimsPrincipal(claimsIdentity),
                    authProperties);

                return RedirectToAction("Index", "Dashboard");
            }

            // Candidate Check
            var subject = await _context.DataSubjects.FirstOrDefaultAsync(s => s.Email == model.Email);
            if (subject != null)
            {
                var hasher = new Microsoft.AspNetCore.Identity.PasswordHasher<DataSubject>();
                var result = hasher.VerifyHashedPassword(subject, subject.Password ?? "", model.Password);

                if (result == Microsoft.AspNetCore.Identity.PasswordVerificationResult.Success)
                {
                    var claims = new List<Claim>
                    {
                        new Claim(ClaimTypes.NameIdentifier, subject.Id.ToString()),
                        new Claim(ClaimTypes.Name, $"{subject.FirstName} {subject.LastName}"),
                        new Claim(ClaimTypes.Email, subject.Email),
                        new Claim(ClaimTypes.Role, "Candidate")
                    };

                    var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                    var authProperties = new AuthenticationProperties { IsPersistent = false };

                    await HttpContext.SignInAsync(
                        CookieAuthenticationDefaults.AuthenticationScheme,
                        new ClaimsPrincipal(claimsIdentity),
                        authProperties);

                    return RedirectToAction("Index", "CandidatePanel");
                }
            }

            ModelState.AddModelError(string.Empty, "Geçersiz giriş denemesi.");
            return View(model);
        }

        [HttpGet]
        public IActionResult Register()
        {
            if (User.Identity != null && User.Identity.IsAuthenticated)
            {
                if (User.IsInRole("Admin")) return RedirectToAction("Index", "Dashboard");
                return RedirectToAction("Index", "CandidatePanel");
            }
            return View();
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Register(RegisterViewModel model)
        {
            if (!model.IsKvkkAccepted)
            {
                ModelState.AddModelError("IsKvkkAccepted", "KVKK onayı gerekmekte.");
            }

            if (!ModelState.IsValid) return View(model);

            var existingSubject = await _context.DataSubjects.AnyAsync(s => s.Email == model.Email);
            if (existingSubject)
            {
                ModelState.AddModelError("Email", "Bu email adresi zaten sisteme kayıtlı.");
                return View(model);
            }

            var hasher = new Microsoft.AspNetCore.Identity.PasswordHasher<DataSubject>();
            
            var subject = new DataSubject
            {
                FirstName = model.FirstName,
                LastName = model.LastName,
                Email = model.Email,
                CreatedAt = DateTime.Now,
                IsAnonymized = false,
                KvkkConsentDate = DateTime.Now,
                ConsentIpAddress = HttpContext.Connection.RemoteIpAddress?.ToString() ?? "Bilinmiyor"
            };
            subject.Password = hasher.HashPassword(subject, model.Password);

            _context.DataSubjects.Add(subject);
            await _context.SaveChangesAsync(); // Get ID

            var tcknEntry = new PersonalDataEntry
            {
                SubjectId = subject.Id,
                CategoryId = 1, // Kimlik Verisi
                DataValue = model.Tckn,
                CollectedAt = DateTime.Now,
                ExpirationDate = DateTime.Now.AddYears(10),
                Status = "ACTIVE"
            };
            _context.PersonalDataEntries.Add(tcknEntry);

            var phoneEntry = new PersonalDataEntry
            {
                SubjectId = subject.Id,
                CategoryId = 2, // İletişim Verisi
                DataValue = model.Phone,
                CollectedAt = DateTime.Now,
                ExpirationDate = DateTime.Now.AddYears(5),
                Status = "ACTIVE"
            };
            _context.PersonalDataEntries.Add(phoneEntry);

            if (model.IsKvkkAccepted)
            {
                var consentLog = new ConsentLog
                {
                    SubjectId = subject.Id,
                    CategoryId = 2, // İletişim Verisi rızası vb.
                    ConsentDate = DateTime.Now,
                    IsRevoked = false
                };
                _context.ConsentLogs.Add(consentLog);
            }
            
            _context.AuditLogs.Add(new AuditLog
            {
                TableName = "DataSubjects",
                RecordId = subject.Id,
                Action = "INSERT",
                ActionDate = DateTime.Now,
                PerformedBy = "System_Register",
                Details = $"Yeni aday kaydı (Aday Portal). Email: {model.Email}"
            });

            await _context.SaveChangesAsync();
            
            TempData["SuccessMessage"] = "Kayıt işleminiz başarıyla tamamlandı. Lütfen giriş yapınız.";
            return RedirectToAction("Login");
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Logout()
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToAction("Index", "Home");
        }
    }
}
