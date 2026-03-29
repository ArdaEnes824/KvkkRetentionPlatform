using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class ConsentLog
{
    public int Id { get; set; }

    public int SubjectId { get; set; }

    public int CategoryId { get; set; }

    public DateTime ConsentDate { get; set; }

    public bool IsRevoked { get; set; }

    public DateTime? RevokedAt { get; set; }

    public virtual DataCategory Category { get; set; } = null!;

    public virtual DataSubject Subject { get; set; } = null!;
}
