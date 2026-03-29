using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class VwExpiredDataForAction
{
    public int EntryId { get; set; }

    public string SubjectName { get; set; } = null!;

    public string Email { get; set; } = null!;

    public string CategoryName { get; set; } = null!;

    public string DataValue { get; set; } = null!;

    public DateTime? ExpirationDate { get; set; }

    public string RequiredAction { get; set; } = null!;

    public int? DaysOverdue { get; set; }
}
