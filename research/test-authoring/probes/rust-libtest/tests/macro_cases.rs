use stream::ensure_bytes;

macro_rules! refuses_negative {
    ($($name:ident: $n:expr,)*) => {
        $(
            #[test]
            fn $name() {
                assert_eq!(ensure_bytes($n), 0);
            }
        )*
    };
}

refuses_negative! {
    minus_one: -1,
    minus_two: -2,
}
