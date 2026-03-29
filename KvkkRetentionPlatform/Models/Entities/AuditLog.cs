using System;
using System.Collections.Generic;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class AuditLog
{
    public int Id { get; set; }

    public string TableName { get; set; } = null!;

    public int RecordId { get; set; }

    public string Action { get; set; } = null!;

    public DateTime ActionDate { get; set; }

    public string PerformedBy { get; set; } = null!;

    public string? Details { get; set; }
}
