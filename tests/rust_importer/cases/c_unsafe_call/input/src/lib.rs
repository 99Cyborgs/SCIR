unsafe fn unsafe_ping() -> i32 {
    7
}

pub fn call_unsafe_ping() -> i32 {
    unsafe { unsafe_ping() }
}
