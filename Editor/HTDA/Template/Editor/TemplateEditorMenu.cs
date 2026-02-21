#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace HTDA.Framework.Template.Editor
{
    public static class TemplateEditorMenu
    {
        [MenuItem("HTDA/Framework/Template/About", priority = 1)]
        public static void About()
        {
            Debug.Log("HTDA.Framework.Template (editor) is initialized. Replace this with your module tools.");
        }
    }
}
#endif