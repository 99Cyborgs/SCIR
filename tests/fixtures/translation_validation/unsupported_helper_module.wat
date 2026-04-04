(module
  (import "env" "helper" (func $helper))
  (func $identity (export "identity") (param $x i32) (result i32)
    local.get $x
  )
  (func $call_identity (export "call_identity") (param $x i32) (result i32)
    local.get $x
    call $identity
  )
)
