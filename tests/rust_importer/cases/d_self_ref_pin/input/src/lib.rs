use std::marker::PhantomPinned;
use std::pin::Pin;

pub struct SelfRef {
    pub data: String,
    pub ptr: *const String,
    pub _pin: PhantomPinned,
}

pub fn make_self_ref(_data: String) -> Pin<Box<SelfRef>> {
    unimplemented!()
}
