pub struct Counter {
    pub value: i32,
}

pub fn clamp_counter(counter: &mut Counter) -> i32 {
    if counter.value < 0 {
        counter.value = 0;
    }
    counter.value
}
