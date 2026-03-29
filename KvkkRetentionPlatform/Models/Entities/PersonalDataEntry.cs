using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class PersonalDataEntry
{
    public int Id { get; set; }

    public int SubjectId { get; set; }

    public int CategoryId { get; set; }

    public string DataValue { get; set; } = null!;

    public DateTime CollectedAt { get; set; }

    public DateTime? ExpirationDate { get; set; }

    public string Status { get; set; } = null!;

    public virtual DataCategory Category { get; set; } = null!;

    public virtual DataSubject Subject { get; set; } = null!;
}
