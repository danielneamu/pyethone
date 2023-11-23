<!-- index.html -->
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python-PHP Example</title>
</head>

<body>
    <button onclick="runPythonScript()">Run Python Script</button>
    <div id="output"></div>

    <script>
        async function runPythonScript() {
            // Call the PHP script using AJAX
            const response = await fetch('run_python.php');
            const result = await response.json();

            if (result.success) {
                document.getElementById('output').innerText = result.output.join('\n');
            } else {
                document.getElementById('output').innerText = 'Error: ' + result.error;
            }
        }
    </script>
</body>

</html>