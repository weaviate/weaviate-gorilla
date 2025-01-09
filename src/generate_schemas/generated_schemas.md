# Generated Database Schemas

## Schema Set 1

**Overview:** This schema focuses on enabling users to discover restaurants based on a comprehensive profile. With semantic search, users can find restaurants by cuisine, ambiance, or special features.

### Restaurants

| Property | Type | Description |
|----------|------|-------------|
| name | string | The name of the restaurant. |
| description | string | A detailed description and summary of the restaurant, including cuisine type and ambiance. |
| averageRating | number | The average rating score out of 5 for the restaurant. |
| openNow | boolean | A flag indicating whether the restaurant is currently open. |

**Use Case:** This schema focuses on enabling users to discover restaurants based on a comprehensive profile. With semantic search, users can find restaurants by cuisine, ambiance, or special features.

### Menus

| Property | Type | Description |
|----------|------|-------------|
| menuItem | string | The name of the menu item. |
| itemDescription | string | A detailed description of the menu item, including ingredients and preparation style. |
| price | number | The price of the menu item. |
| isVegetarian | boolean | A flag to indicate if the menu item is vegetarian. |

**Use Case:** This schema assists in linking dining experiences with specific restaurants through their menus. Rich search features allow customers to find dishes tailored to dietary needs and price points.

### Reservations

| Property | Type | Description |
|----------|------|-------------|
| reservationName | string | The name under which the reservation is made. |
| notes | string | Detailed notes about the reservation, such as special requests or celebrations. |
| partySize | number | The number of persons in the reservation. |
| confirmed | boolean | A flag indicating whether the reservation is confirmed. |

**Use Case:** This schema integrates with the restaurants by managing booking experiences. Semantic search of reservations can uncover trends in dining preferences and commonly requested meal attributes.

---

## Schema Set 2

**Overview:** This schema aims to help users discover clinics based on services, specialties, and patient satisfaction. Semantic search can be used to find clinics by specific healthcare needs or service qualities.

### Clinics

| Property | Type | Description |
|----------|------|-------------|
| clinicName | string | The official name of the clinic. |
| description | string | A detailed overview of the clinic, including specialties and services offered. |
| averagePatientSatisfaction | number | The average patient satisfaction score for the clinic. |
| acceptingNewPatients | boolean | Indicates whether the clinic is currently accepting new patients. |

**Use Case:** This schema aims to help users discover clinics based on services, specialties, and patient satisfaction. Semantic search can be used to find clinics by specific healthcare needs or service qualities.

### Doctors

| Property | Type | Description |
|----------|------|-------------|
| doctorName | string | The full name of the doctor. |
| expertise | string | A detailed description of the doctor's areas of medical expertise and specialties. |
| yearsOfExperience | number | The number of years of experience the doctor has. |
| currentlyPracticing | boolean | A flag indicating if the doctor is currently practicing at any clinic. |

**Use Case:** This schema supports finding doctors based on expertise and experience. With semantic search, users can match their health concerns to the right professionals by exploring detailed profiles.

### Appointments

| Property | Type | Description |
|----------|------|-------------|
| patientName | string | The name of the patient who booked the appointment. |
| appointmentNotes | string | Detailed notes about the appointment including purpose and any special requests. |
| appointmentDuration | number | The duration of the appointment in minutes. |
| appointmentConfirmed | boolean | Indicates whether the appointment is confirmed. |

**Use Case:** This schema is designed to manage and optimize booking experiences by allowing semantic searches for specific appointment details and patient booking patterns.

---

## Schema Set 3

**Overview:** This schema helps users find courses based on subject matter, duration, and enrollment status. Semantic search enhances discovery of courses by learning outcomes and topics covered.

### Courses

| Property | Type | Description |
|----------|------|-------------|
| courseTitle | string | The title of the course. |
| courseDescription | string | A detailed summary of the course, including coverage topics and learning outcomes. |
| courseDuration | number | The total number of hours required to complete the course. |
| currentlyEnrolling | boolean | Indicates whether the course is currently open for enrollment. |

**Use Case:** This schema helps users find courses based on subject matter, duration, and enrollment status. Semantic search enhances discovery of courses by learning outcomes and topics covered.

### Instructors

| Property | Type | Description |
|----------|------|-------------|
| instructorName | string | The full name of the instructor. |
| biography | string | A detailed biography of the instructor, including professional background and teaching philosophy. |
| yearsOfTeaching | number | The number of years the instructor has been teaching. |
| tenured | boolean | Indicates whether the instructor holds a tenured position. |

**Use Case:** This schema allows students and administrators to search for instructors based on experience and background. Rich biographies help in matching students with instructors who align with their learning style and academic goals.

### Students

| Property | Type | Description |
|----------|------|-------------|
| studentName | string | The full name of the student. |
| researchInterests | string | Detailed information on the student's academic interests and research focus. |
| completedCredits | number | The number of academic credits the student has completed. |
| enrolledFullTime | boolean | Indicates whether the student is enrolled full-time. |

**Use Case:** This schema is designed to help institutions manage student data and preferences. Semantic search allows deeper insights into student research interests and progression paths.

---

## Schema Set 4

**Overview:** This schema allows users to explore travel destinations based on detailed descriptions and average costs. Semantic search can help users find destinations that match desired experiences or budget levels.

### TravelDestinations

| Property | Type | Description |
|----------|------|-------------|
| destinationName | string | The name of the travel destination. |
| destinationDescription | string | A detailed description of the destination including attractions, culture, and climate. |
| averageVisitCost | number | The average cost of a trip to the destination. |
| popular | boolean | Indicates whether the destination is currently popular among tourists. |

**Use Case:** This schema allows users to explore travel destinations based on detailed descriptions and average costs. Semantic search can help users find destinations that match desired experiences or budget levels.

### TravelAgents

| Property | Type | Description |
|----------|------|-------------|
| agentName | string | The full name of the travel agent. |
| agentDescription | string | A detailed description of the agent's expertise, including specialties and customer reviews. |
| yearsOfExperience | number | The number of years the agent has been in the industry. |
| availableNow | boolean | Indicates whether the travel agent is currently available for consultation. |

**Use Case:** This schema supports customers in finding travel agents based on expertise and availability. Semantic search enables matching with agents who have specific regional knowledge or customer service excellence.

### TravelPackages

| Property | Type | Description |
|----------|------|-------------|
| packageName | string | The name of the travel package. |
| packageDetails | string | A comprehensive description of the travel package, including itinerary and included services. |
| packagePrice | number | The total price of the travel package. |
| discountAvailable | boolean | Indicates whether there is a discount available on the package. |

**Use Case:** This schema helps travelers find travel packages based on detailed descriptions and pricing. Semantic search allows for discovering packages that align with preferences for activities or budget constraints.

---

## Schema Set 5

**Overview:** The Museums schema provides an enriching database for those interested in exploring detailed cultural exhibits. Semantic search capabilities highlight unique features and historical value of the museum's collections.

### Museums

| Property | Type | Description |
|----------|------|-------------|
| museumName | string | The name of the museum. |
| exhibitHighlights | string | A detailed description of the museum's most notable exhibits and their historical significance. |
| entryFee | number | The standard entry fee for the museum. |
| openToday | boolean | A flag indicating if the museum is open today. |

**Use Case:** The Museums schema provides an enriching database for those interested in exploring detailed cultural exhibits. Semantic search capabilities highlight unique features and historical value of the museum's collections.

### Exhibitions

| Property | Type | Description |
|----------|------|-------------|
| exhibitionTitle | string | The title of the exhibition. |
| exhibitionDescription | string | A comprehensive overview of the exhibition, including themes and featured artworks. |
| averageVisitorCount | number | The average number of visitors per day for the exhibition. |
| currentlyRunning | boolean | Indicates whether the exhibition is currently open to the public. |

**Use Case:** This schema helps users discover and explore various exhibitions based on thematic interest or visitor popularity, encouraging semantic searches for immersive cultural experiences.

### ArtPieces

| Property | Type | Description |
|----------|------|-------------|
| artPieceName | string | The name of the art piece. |
| artPieceHistory | string | A detailed history and description of the art piece, including the artist and creation story. |
| currentValuation | number | The current market valuation of the art piece. |
| onDisplay | boolean | A flag indicating if the art piece is currently on display. |

**Use Case:** The ArtPieces schema supports the discovery and assessment of art pieces across various museums. With semantic capabilities, users can explore artwork based on historical significance and monetary valuation.

---

