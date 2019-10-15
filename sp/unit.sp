import "unittest"

@Test
fn t1() {
    assert 1 == 1;
}

@Test
fn t2() {
    assert 1 ==2;
}

unittest.testall();
