use std::path::Path;

fn main() {
    let id = "../../../etc/passwd";
    if id.contains('/') || id.contains('\\') || id.contains("..") {
        println!("Invalid session ID");
    } else {
        println!("Valid session ID");
    }
}
