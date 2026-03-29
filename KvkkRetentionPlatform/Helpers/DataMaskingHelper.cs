namespace KvkkRetentionPlatform.Helpers
{
    public static class DataMaskingHelper
    {
        public static string MaskData(string input)
        {
            if (string.IsNullOrEmpty(input)) return input;

            if (input.Contains("@"))
            {
                var parts = input.Split('@');
                if (parts[0].Length > 2)
                {
                    parts[0] = parts[0].Substring(0, 2) + new string('*', parts[0].Length - 2);
                }
                return string.Join("@", parts);
            }
            
            if (input.Length > 4)
            {
                var first = input.Substring(0, 3);
                var last = input.Substring(input.Length - 4);
                return first + new string('*', input.Length - 7 > 0 ? input.Length - 7 : 3) + last;
            }

            return new string('*', input.Length);
        }
    }
}
