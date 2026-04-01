pub fn clamp_nonneg(x: i32) -> i32 {
    let mut y = x;
    if y < 0 {
        y = 0;
    }
    y
}
