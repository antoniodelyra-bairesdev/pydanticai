import "./JSONText.css";

function syntaxHighlight(json: Record<string, any> | string) {
  const str = (typeof json === "string" ? json : JSON.stringify(json, null, 2))
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return str.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    function (match) {
      var cls = "number";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "key";
        } else {
          cls = "string";
        }
      } else if (/true|false/.test(match)) {
        cls = "boolean";
      } else if (/null/.test(match)) {
        cls = "null";
      }
      return '<span class="' + cls + '">' + match + "</span>";
    },
  );
}

export default function JSONText({
  json,
}: {
  json: Record<string, any> | string;
}) {
  return (
    <pre dangerouslySetInnerHTML={{ __html: syntaxHighlight(json) }}></pre>
  );
}
