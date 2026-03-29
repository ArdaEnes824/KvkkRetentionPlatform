using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using KvkkRetentionPlatform.Models.Entities;
using System.Linq;
using System.Threading.Tasks;

namespace KvkkRetentionPlatform.Controllers
{
    public class AuditLogsController : Controller
    {
        private readonly KvkkDbContext _context;

        public AuditLogsController(KvkkDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var logs = await _context.AuditLogs
                .OrderByDescending(x => x.ActionDate)
                .ToListAsync();
            return View(logs);
        }
    }
}
