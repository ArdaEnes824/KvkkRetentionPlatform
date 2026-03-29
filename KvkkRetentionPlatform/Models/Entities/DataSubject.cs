using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class DataSubject
{
    public int Id { get; set; }

    public string FirstName { get; set; } = null!;

    public string LastName { get; set; } = null!;

    public string Email { get; set; } = null!;

    public string? Password { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime? KvkkConsentDate { get; set; }

    public string? ConsentIpAddress { get; set; }

    public bool IsAnonymized { get; set; }

    public virtual ICollection<ConsentLog> ConsentLogs { get; set; } = new List<ConsentLog>();

    public virtual ICollection<PersonalDataEntry> PersonalDataEntries { get; set; } = new List<PersonalDataEntry>();

    public virtual ICollection<JobApplication> JobApplications { get; set; } = new List<JobApplication>();
}
