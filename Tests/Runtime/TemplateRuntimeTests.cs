using NUnit.Framework;

namespace HTDA.Framework.Template.Tests
{
    public class TemplateRuntimeTests
    {
        [Test]
        public void PackageInfo_Name_IsNotEmpty()
        {
            Assert.IsFalse(string.IsNullOrEmpty(HTDA.Framework.Template.PackageInfo.Name));
        }
    }
}