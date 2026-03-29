using KvkkRetentionPlatform.Models.Entities;

namespace KvkkRetentionPlatform.Models
{
    public class CandidatePanelViewModel
    {
        public DataSubject Subject { get; set; } = null!;
        public string MaskedTckn { get; set; } = null!;
        public string MaskedPhone { get; set; } = null!;
        public bool IsConsentActive { get; set; }
    }
}
