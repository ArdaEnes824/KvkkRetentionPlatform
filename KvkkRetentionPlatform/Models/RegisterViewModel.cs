using System.ComponentModel.DataAnnotations;

namespace KvkkRetentionPlatform.Models
{
    public class RegisterViewModel
    {
        [Required(ErrorMessage = "Ad alanı zorunludur.")]
        public string FirstName { get; set; } = null!;

        [Required(ErrorMessage = "Soyad alanı zorunludur.")]
        public string LastName { get; set; } = null!;

        [Required(ErrorMessage = "Email alanı zorunludur.")]
        [EmailAddress(ErrorMessage = "Geçerli bir email adresi giriniz.")]
        public string Email { get; set; } = null!;

        [Required(ErrorMessage = "TCKN alanı zorunludur.")]
        [StringLength(11, MinimumLength = 11, ErrorMessage = "TCKN 11 haneli olmalıdır.")]
        public string Tckn { get; set; } = null!;

        [Required(ErrorMessage = "Telefon alanı zorunludur.")]
        public string Phone { get; set; } = null!;

        [Required(ErrorMessage = "Şifre alanı zorunludur.")]
        [DataType(DataType.Password)]
        public string Password { get; set; } = null!;

        [Required(ErrorMessage = "KVKK onayı gerekmekte.")]
        public bool IsKvkkAccepted { get; set; }
    }
}
