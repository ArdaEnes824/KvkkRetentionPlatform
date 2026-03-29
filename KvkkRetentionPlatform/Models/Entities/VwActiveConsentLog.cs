using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class VwActiveConsentLog
{
    public int ConsentId { get; set; }

    public int SubjectId { get; set; }

    public string SubjectFullName { get; set; } = null!;

    public string CategoryName { get; set; } = null!;

    public DateTime ConsentDate { get; set; }

    public int? MonthsSinceConsent { get; set; }
}
