fn main(){
    let price=24500.00;

    let quantity=10;

    let trade_value=price*quantity as f64;
    println!("Nifty price: {}",price);
    println!("Quantity: {}",quantity);
    println!("The trade value is: {}",trade_value);
}