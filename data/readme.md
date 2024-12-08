# Schemas

| Domain | Collection | Property | Data Type | Description |
|--------|------------|-----------|------------|-------------|
| Dining | Restaurants | name | string | The name of the restaurant |
| | | description | string | Detailed description and summary, including cuisine type and ambiance |
| | | averageRating | number | Average rating score out of 5 |
| | | openNow | boolean | Whether the restaurant is currently open |
| | Menus | menuItem | string | The name of the menu item |
| | | itemDescription | string | Detailed description including ingredients and preparation |
| | | price | number | The price of the menu item |
| | | isVegetarian | boolean | Whether the menu item is vegetarian |
| | Reservations | reservationName | string | Name under which reservation is made |
| | | notes | string | Special requests or celebration details |
| | | partySize | number | Number of persons |
| | | confirmed | boolean | Whether reservation is confirmed |
| Healthcare | Clinics | clinicName | string | Official name of the clinic |
| | | description | string | Overview of specialties and services |
| | | averagePatientSatisfaction | number | Average patient satisfaction score |
| | | acceptingNewPatients | boolean | Whether accepting new patients |
| | Doctors | doctorName | string | Full name of the doctor |
| | | expertise | string | Areas of medical expertise and specialties |
| | | yearsOfExperience | number | Years of experience |
| | | currentlyPracticing | boolean | Whether currently practicing |
| | Appointments | patientName | string | Patient name |
| | | appointmentNotes | string | Purpose and special requests |
| | | appointmentDuration | number | Duration in minutes |
| | | appointmentConfirmed | boolean | Whether appointment is confirmed |
| Education | Courses | courseTitle | string | Title of the course |
| | | courseDescription | string | Coverage topics and learning outcomes |
| | | courseDuration | number | Total hours to complete |
| | | currentlyEnrolling | boolean | Whether open for enrollment |
| | Instructors | instructorName | string | Full name of instructor |
| | | biography | string | Professional background and teaching philosophy |
| | | yearsOfTeaching | number | Years of teaching experience |
| | | tenured | boolean | Whether holds tenured position |
| | Students | studentName | string | Full name of student |
| | | researchInterests | string | Academic interests and research focus |
| | | completedCredits | number | Completed academic credits |
| | | enrolledFullTime | boolean | Whether enrolled full-time |
| Travel | TravelDestinations | destinationName | string | Name of destination |
| | | destinationDescription | string | Attractions, culture, and climate details |
| | | averageVisitCost | number | Average trip cost |
| | | popular | boolean | Whether currently popular |
| | TravelAgents | agentName | string | Full name of agent |
| | | agentDescription | string | Expertise and customer reviews |
| | | yearsOfExperience | number | Years in industry |
| | | availableNow | boolean | Whether available for consultation |
| | TravelPackages | packageName | string | Name of travel package |
| | | packageDetails | string | Itinerary and included services |
| | | packagePrice | number | Total package price |
| | | discountAvailable | boolean | Whether discount is available |
| Culture | Museums | museumName | string | Name of museum |
| | | exhibitHighlights | string | Notable exhibits and historical significance |
| | | entryFee | number | Standard entry fee |
| | | openToday | boolean | Whether open today |
| | Exhibitions | exhibitionTitle | string | Title of exhibition |
| | | exhibitionDescription | string | Themes and featured artworks |
| | | averageVisitorCount | number | Average daily visitors |
| | | currentlyRunning | boolean | Whether currently open |
| | ArtPieces | artPieceName | string | Name of art piece |
| | | artPieceHistory | string | Artist and creation story |
| | | currentValuation | number | Current market value |
| | | onDisplay | boolean | Whether currently on display |
