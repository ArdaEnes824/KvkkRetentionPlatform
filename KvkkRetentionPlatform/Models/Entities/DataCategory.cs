using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class DataCategory
{
    public int Id { get; set; }

    public string CategoryName { get; set; } = null!;

    public string? Description { get; set; }

    public virtual ICollection<ConsentLog> ConsentLogs { get; set; } = new List<ConsentLog>();

    public virtual ICollection<PersonalDataEntry> PersonalDataEntries { get; set; } = new List<PersonalDataEntry>();

    public virtual ICollection<RetentionPolicy> RetentionPolicies { get; set; } = new List<RetentionPolicy>();
}
