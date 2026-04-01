async fn fetch_value() -> i32 {
    1
}

pub async fn load_once() -> i32 {
    fetch_value().await
}
