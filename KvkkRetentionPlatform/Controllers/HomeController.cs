using System.Diagnostics;
using KvkkRetentionPlatform.Models;
using KvkkRetentionPlatform.Models.Entities;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;

namespace KvkkRetentionPlatform.Controllers
{
    [AllowAnonymous]
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;
        private readonly KvkkDbContext _context;

        public HomeController(ILogger<HomeController> logger, KvkkDbContext context)
        {
            _logger = logger;
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var jobs = await _context.JobPostings
                .Where(j => j.Status == "Açık")
                .OrderByDescending(j => j.CreatedAt)
                .Take(3)
                .ToListAsync();
                
            return View(jobs);
        }


        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
