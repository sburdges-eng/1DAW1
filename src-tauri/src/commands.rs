use serde::{Deserialize, Serialize};
use tauri::command;

#[derive(Debug, Serialize, Deserialize)]
pub struct EmotionalIntent {
    pub core_wound: Option<String>,
    pub core_desire: Option<String>,
    #[serde(default)]
    pub emotional_intent: Option<String>,  // Legacy field
    pub technical: Option<serde_json::Value>,
    // New format: base_emotion, intensity, specific_emotion
    pub base_emotion: Option<String>,
    pub intensity: Option<String>,
    pub specific_emotion: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerateRequest {
    pub intent: EmotionalIntent,
    pub output_format: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InterrogateRequest {
    pub message: String,
    pub session_id: Option<String>,
    pub context: Option<serde_json::Value>,
}

#[command]
pub async fn generate_music(request: GenerateRequest) -> Result<serde_json::Value, String> {
    crate::bridge::musicbrain::generate(request)
        .await
        .map_err(|e| e.to_string())
}

#[command]
pub async fn interrogate(request: InterrogateRequest) -> Result<serde_json::Value, String> {
    crate::bridge::musicbrain::interrogate(request)
        .await
        .map_err(|e| e.to_string())
}

#[command]
pub async fn get_emotions() -> Result<serde_json::Value, String> {
    crate::bridge::musicbrain::get_emotions()
        .await
        .map_err(|e| e.to_string())
}
