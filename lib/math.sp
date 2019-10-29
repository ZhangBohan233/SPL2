import "functions"


const E = 2.718281828459045;
const PI = 3.141592653589793;


/*
 * Returns a random `float` number between <0> and <1>.
 */
fn random() {
    const m = (1 << 15) - 1;
    const a = 3;
    var seed = system.time();
    for var i = 0; i < 100; i++ {
        seed = seed * a % m;
    }
    return float(seed) / 32768;
}


/*
 * Returns the absolute value of <n>.
 */
fn abs(n) {
    if n >= 0 {
        return n;
    } else {
        return -n;
    }
}


fn ceil(n) {
    var x = int(n);
    if n > x {
        return x + 1;
    } else {
        return x;
    }
}


fn floor(n) {
    return int(n);
}


/*
 * Returns the greatest common divisor of x and y.
 */
fn gcd(x, y) {
    if x != int(x) || y != int(y) {
        throw new MathException("gcd(x, y) only works for integers.");
    }
    var abs_a = abs(x);
    var abs_b = abs(y);
    var q, b;
    if abs_a < abs_b {
        q = abs_b;
        b = abs_a;
    } else {
        q = abs_a;
        b = abs_b;
    }
    if b == 0 {
        return q;
    }
    var r;
    while (r = q % b) != 0 {
        q = b;
        b = r;
    }
    return b;
}


fn log(x, base=null) {
    if base === null {
        return natives.log(x);
    } else {
        return natives.log(x) / natives.log(base);
    }
}


/*
 * Returns <exp> power of <base>.
 */
fn pow(base, exp) {
    return natives.pow(base, exp);
}


/*
 * Returns the square root of <n>.
 */
fn sqrt(n) {
    var x = float(n);
    var g = x;
    while abs(g * g - x) > 0.000001 {
        g = (g + x / g) / 2;
    }
    return g;
}


/*
 * Returns the nearest integer of number <n>.
 */
fn round(n) {
    var fl = floor(n);
    var ce = ceil(n);
    var low = n - fl;
    var up = ce - n;
    if up > low {
        return fl;
    } else {
        return ce;
    }
}


/*
 * Returns the number of combination picking <k> from <n>;
 */
fn comb(n, k) {
    return perm(n, k) / fact(k);
}


/*
 * Returns the number of permutation picking <k> from <n>;
 */
fn perm(n, k) {
    return fact(n) / fact(n - k);
}


/*
 * Returns the factorial of <n>.
 */
fn factorial(n) {
	if n <= 1 return 1;
	else return n * factorial(n - 1);
}


/*
 * Returns the factorial of <n>.
 */
fn fact(n) {
    var x = 1;
    for var i = 1; i <= n; i++ {
        x *= i;
    }
    return x;
}


/*
 * Returns <true> if <p> is a prime.
 */
fn isPrime(p) {
    var lim = ceil(sqrt(p));
    if p == 2 {
        return true;
    } else if p % 2 == 0 {
        return false;
    } else {
        for factor := 3; factor < lim; factor += 2 {
            if p % factor == 0 {
                return false;
            }
        }
        return true;
    }
}


/*
 * Returns a list of primes that less than or equal to <limit>.
 */
fn primes(limit) {
    var lst = [];
    for var i = 2; i <= limit; i++ {
        lst.append(i);
    }
    var index = 0;
    var tar = lst[0];
    while lst[lst.size() - 1] > tar * tar {
        tar = lst[index];
        lst = functions.filter(lst, x -> x == tar || x % tar != 0);
        index += 1;
    }
    return lst;
}


fn eulerPhi(n) {
    var count = 0;
    for var i = 0; i < n; i++ {
        if gcd(n, i) == 1 {
            count++;
        }
    }
    return count;
}


fn eulerPhiFp(n) {
    return functions.count(range(1, n, 1), x -> gcd(n, x) == 1);
}


fn eulerPhi2(n) {
    fac := factorization(n);
    sum := 1;
    for var p; fac {
        sum *= 1 - 1.0 / p;
    }
    return int(n * sum);
}


fn cos(x) {
    return natives.cos(x);
}


fn sin(x) {
    return cos(PI/2 - x);
}


fn tan(x) {
    return sin(x) / cos(x);
}


fn rad(x) {
    return x * PI / 180;
}


fn deg(x) {
    return x * 180 / PI;
}


fn acos(n) {
    return PI / 2 - asin(n);
}


fn asin(n) {
    return natives.asin(n);
}


fn atan(n) {
    return natives.atan(n);
}


/*
 * Returns the prime factorization of integer <n>.
 */
fn factorization(n) {
    var x = n;
    var ps = primes(n);
    var res = pair();
    if ps[ps.size() - 1] == n {
        res[n] = 1;
        return res;
    }
    while x > 1 {
        for var p; ps {
            if x % p == 0 {
                x /= p;
                if res.contains(p) {
                    res[p] = res[p] + 1;
                } else {
                    res[p] = 1;
                }
                break;
            }
        }
    }
    return res;
}


fn fib(n) {
    if (n < 2) {
        return n;
    } else {
        return fib(n - 1) + fib(n - 2);
    }
}


class MathException extends Exception {
    fn MathException(msg="") {
        Exception(msg);
    }
}
