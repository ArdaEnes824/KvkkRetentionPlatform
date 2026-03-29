using System.ComponentModel.DataAnnotations;

namespace KvkkRetentionPlatform.Models
{
    public class LoginViewModel
    {
        [Required(ErrorMessage = "Email alanı zorunludur.")]
        [EmailAddress(ErrorMessage = "Geçerli bir email adresi giriniz.")]
        public string Email { get; set; } = null!;

        [Required(ErrorMessage = "Şifre alanı zorunludur.")]
        [DataType(DataType.Password)]
        public string Password { get; set; } = null!;

        public bool RememberMe { get; set; }
    }
}
