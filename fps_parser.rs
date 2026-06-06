fn main(){
    let feed_format=String::from("NC^7208^12345^24500.50");
    let feed_format_vec:Vec<&str>=feed_format.split("^").collect();
    let symbol=feed_format_vec[0];
    let trans_code=parse_int(feed_format_vec[1]);
    let scrip_code=parse_int(feed_format_vec[2]);
    let price=parse_float(feed_format_vec[3]);

    println!("Symbol: {}",symbol);
    println!("Transaction code: {}",trans_code);
    println!("Scrip code: {}",scrip_code);
    println!("Price: {}",price);



}

fn parse_int(s:&str)->i32{
    s.parse::<i32>().unwrap_or(0)
}

fn parse_float(s:&str)->f64{
    s.parse::<f64>().unwrap_or(0.0)
}