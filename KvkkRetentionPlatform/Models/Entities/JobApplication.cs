using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace KvkkRetentionPlatform.Models.Entities
{
    public class JobApplication
    {
        public int Id { get; set; }
        
        public int SubjectId { get; set; }
        public int JobPostingId { get; set; }
        
        public DateTime ApplicationDate { get; set; } = DateTime.Now;
        
        [MaxLength(50)]
        public string Status { get; set; } = "Bekleniyor";

        [ForeignKey("SubjectId")]
        public virtual DataSubject Subject { get; set; } = null!;
        
        [ForeignKey("JobPostingId")]
        public virtual JobPosting JobPosting { get; set; } = null!;
    }
}
