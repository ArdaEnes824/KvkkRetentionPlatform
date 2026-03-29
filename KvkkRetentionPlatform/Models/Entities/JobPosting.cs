using System;
using System.ComponentModel.DataAnnotations;

namespace KvkkRetentionPlatform.Models.Entities
{
    public class JobPosting
    {
        public int Id { get; set; }
        
        [Required]
        [MaxLength(200)]
        public string Title { get; set; } = null!;
        
        [Required]
        public string Description { get; set; } = null!;
        
        [Required]
        [MaxLength(100)]
        public string Department { get; set; } = null!;
        
        [MaxLength(50)]
        public string Status { get; set; } = "Açık";
        
        public DateTime CreatedAt { get; set; } = DateTime.Now;
    }
}
