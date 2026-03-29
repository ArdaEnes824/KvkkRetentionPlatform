using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class RetentionPolicy
{
    public int Id { get; set; }

    public int CategoryId { get; set; }

    public int RetentionMonths { get; set; }

    public string ActionType { get; set; } = null!;

    public bool IsActive { get; set; }

    public virtual DataCategory Category { get; set; } = null!;
}
