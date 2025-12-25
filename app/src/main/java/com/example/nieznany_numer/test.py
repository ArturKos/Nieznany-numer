curl -X POST "http://localhost:1234/v1/completions" \
             -H "Authorization: Bearer lm-studio" \
                -H "Content-Type: application/json" \
                   -d '{
"model": "qwen2.5-coder-7b-instruct-mlx",
"prompt": "Clean trivial TODOs in this Kotlin/Java file. Only modify TODOs. Output only the code.\nFile content:\n, \n```kotlin\npackage com.example.nieznany_numer.test.py\n\n// TODO: Remove unused imports\nimport android.os.Bundle\nimport androidx.activity.ComponentActivity\nimport androidx.activity.compose.setContent\nimport androidx.compose.foundation.layout.fillMaxSize\nimport androidx.compose.material3.MaterialTheme\nimport androidx.compose.material3.Surface\nimport androidx.compose.material3.Text\nimport androidx.compose.runtime.Composable\nimport androidx.compose.ui.Modifier\nimport androidx.compose.ui.tooling.preview.Preview\nimport com.example.nieznany_numer.ui.theme.Nieznany_NumerTheme\n\nclass MainActivity : ComponentActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        setContent {\n            Nieznany_NumerTheme {\n                // A surface container using the \'background\' color from the theme\n                Surface(\n                    modifier = Modifier.fillMaxSize(),\n                    color = MaterialTheme.colorScheme.background\n                ) {\n                    Greeting("Android")\n                }\n            }\n        }\n    }\n}\n\n@Composable\nfun Greeting(name: String) {\n    Text(text = "Hello $name!")\n}\n\n@Preview(showBackground = true)\n@Composable\nfun DefaultPreview() {\n    Nieznany_NumerTheme {\n        Greeting("Android")\n    }\n}\n```\nCleaned file content:",
"temperature": 0.2,
"max_tokens": 4096
}'
