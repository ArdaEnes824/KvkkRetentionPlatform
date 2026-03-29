using System.ComponentModel.DataAnnotations;

namespace KvkkRetentionPlatform.Models.Entities
{
    public class User
    {
        public int Id { get; set; }
        
        [MaxLength(11)]
        public string TcKimlikNo { get; set; } = null!;
        
        public string PhoneNumber { get; set; } = null!;
        
        public string Email { get; set; } = null!;
        
        public bool IsKvkkAccepted { get; set; }
    }
}
