use a_mut_local::clamp_nonneg;

#[test]
fn smoke() {
    assert_eq!(clamp_nonneg(-3), 0);
    assert_eq!(clamp_nonneg(4), 4);
}
