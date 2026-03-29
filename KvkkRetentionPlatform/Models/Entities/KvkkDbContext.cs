using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace KvkkRetentionPlatform.Models.Entities;

public partial class KvkkDbContext : DbContext
{
    public KvkkDbContext()
    {
    }

    public KvkkDbContext(DbContextOptions<KvkkDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<AuditLog> AuditLogs { get; set; }

    public virtual DbSet<ConsentLog> ConsentLogs { get; set; }

    public virtual DbSet<DataCategory> DataCategories { get; set; }

    public virtual DbSet<DataSubject> DataSubjects { get; set; }

    public virtual DbSet<PersonalDataEntry> PersonalDataEntries { get; set; }

    public virtual DbSet<RetentionPolicy> RetentionPolicies { get; set; }

    public virtual DbSet<VwActiveConsentLog> VwActiveConsentLogs { get; set; }

    public virtual DbSet<VwExpiredDataForAction> VwExpiredDataForActions { get; set; } = null!;

    public virtual DbSet<User> Users { get; set; } = null!;

    public virtual DbSet<JobPosting> JobPostings { get; set; } = null!;
    
    public virtual DbSet<JobApplication> JobApplications { get; set; } = null!;

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
#warning To protect potentially sensitive information in your connection string, you should move it out of source code. You can avoid scaffolding the connection string by using the Name= syntax to read it from configuration - see https://go.microsoft.com/fwlink/?linkid=2131148. For more guidance on storing connection strings, see https://go.microsoft.com/fwlink/?LinkId=723263.
        => optionsBuilder.UseSqlServer("Server=LAPTOP-6JOBCV4R\\MSSQLSERVER01;Database=KvkkRetentionDb;Trusted_Connection=True;TrustServerCertificate=True;");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<AuditLog>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__AuditLog__3214EC07BFD51593");

            entity.Property(e => e.Action).HasMaxLength(50);
            entity.Property(e => e.ActionDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.PerformedBy).HasMaxLength(100);
            entity.Property(e => e.TableName).HasMaxLength(50);
        });

        modelBuilder.Entity<ConsentLog>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__ConsentL__3214EC073A820DDC");

            entity.Property(e => e.ConsentDate)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.RevokedAt).HasColumnType("datetime");

            entity.HasOne(d => d.Category).WithMany(p => p.ConsentLogs)
                .HasForeignKey(d => d.CategoryId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_ConsentLogs_Categories");

            entity.HasOne(d => d.Subject).WithMany(p => p.ConsentLogs)
                .HasForeignKey(d => d.SubjectId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_ConsentLogs_Subjects");
        });

        modelBuilder.Entity<DataCategory>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__DataCate__3214EC0788A3049A");

            entity.HasIndex(e => e.CategoryName, "UQ__DataCate__8517B2E0CD3BD75D").IsUnique();

            entity.Property(e => e.CategoryName).HasMaxLength(50);
            entity.Property(e => e.Description).HasMaxLength(255);
        });

        modelBuilder.Entity<DataSubject>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__DataSubj__3214EC0760AB92C9");

            entity.HasIndex(e => e.Email, "UQ__DataSubj__A9D10534476B9520").IsUnique();

            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.Email).HasMaxLength(100);
            entity.Property(e => e.Password).HasMaxLength(255);
            entity.Property(e => e.FirstName).HasMaxLength(50);
            entity.Property(e => e.LastName).HasMaxLength(50);
        });

        modelBuilder.Entity<PersonalDataEntry>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Personal__3214EC07F78D1EA9");

            entity.ToTable(tb => tb.HasTrigger("trg_Audit_PersonalDataEntries"));

            entity.Property(e => e.CollectedAt)
                .HasDefaultValueSql("(getdate())")
                .HasColumnType("datetime");
            entity.Property(e => e.ExpirationDate).HasColumnType("datetime");
            entity.Property(e => e.Status)
                .HasMaxLength(20)
                .HasDefaultValue("ACTIVE");

            entity.HasOne(d => d.Category).WithMany(p => p.PersonalDataEntries)
                .HasForeignKey(d => d.CategoryId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_DataEntries_Categories");

            entity.HasOne(d => d.Subject).WithMany(p => p.PersonalDataEntries)
                .HasForeignKey(d => d.SubjectId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_DataEntries_Subjects");
        });

        modelBuilder.Entity<RetentionPolicy>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("PK__Retentio__3214EC07BC8EF961");

            entity.Property(e => e.ActionType).HasMaxLength(20);
            entity.Property(e => e.IsActive).HasDefaultValue(true);

            entity.HasOne(d => d.Category).WithMany(p => p.RetentionPolicies)
                .HasForeignKey(d => d.CategoryId)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_RetentionPolicies_Categories");
        });

        modelBuilder.Entity<VwActiveConsentLog>(entity =>
        {
            entity
                .HasNoKey()
                .ToView("vw_ActiveConsentLogs");

            entity.Property(e => e.CategoryName).HasMaxLength(50);
            entity.Property(e => e.ConsentDate).HasColumnType("datetime");
            entity.Property(e => e.SubjectFullName).HasMaxLength(101);
        });

        modelBuilder.Entity<VwExpiredDataForAction>(entity =>
        {
            entity
                .HasNoKey()
                .ToView("vw_ExpiredDataForAction");

            entity.Property(e => e.CategoryName).HasMaxLength(50);
            entity.Property(e => e.Email).HasMaxLength(100);
            entity.Property(e => e.ExpirationDate).HasColumnType("datetime");
            entity.Property(e => e.RequiredAction).HasMaxLength(20);
            entity.Property(e => e.SubjectName).HasMaxLength(101);
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
