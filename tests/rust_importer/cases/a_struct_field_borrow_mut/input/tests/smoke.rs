use a_struct_field_borrow_mut::{clamp_counter, Counter};

#[test]
fn smoke() {
    let mut counter = Counter { value: -5 };
    assert_eq!(clamp_counter(&mut counter), 0);
    assert_eq!(counter.value, 0);
}
