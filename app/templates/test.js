function testPostDataToServer () {

    fetch("/api/measurements/pico_001",
        {
            method: 'POST', 
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                rainfall: Math.floor(Math.random() * 250 ),
            humidity: Math.floor(Math.random() * 30 + 60),
            temperature: 27
            
        })
    })
    .then(res => res.json())
    .then(data => console.log(data))
    
}