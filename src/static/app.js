document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesList.innerHTML = "";
      // Clear the activity dropdown before repopulating to avoid duplicates
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        const spotsLeft = details.max_participants - details.participants.length;
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants list (no bullets)
        const participantsList = document.createElement("ul");
        participantsList.className = "participants-list";

        details.participants.forEach((email) => {
          const li = document.createElement("li");

          const span = document.createElement("span");
          span.textContent = email;

          const deleteBtn = document.createElement("button");
          deleteBtn.className = "delete-btn";
          deleteBtn.title = "Unregister";
          deleteBtn.type = "button";
          deleteBtn.innerHTML = "🗑️";

          // Per-button listener to unregister and refresh list
          deleteBtn.addEventListener("click", async () => {
            try {
              const delResponse = await fetch(
                `/activities/${encodeURIComponent(name)}/participants/${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );
              if (!delResponse.ok) {
                const err = await delResponse.json().catch(() => ({}));
                messageDiv.textContent = err.detail || "Failed to unregister participant";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
              } else {
                // Refresh activities to reflect change
                await fetchActivities();
              }
            } catch (err) {
              messageDiv.textContent = "Failed to unregister participant";
              messageDiv.className = "error";
              messageDiv.classList.remove("hidden");
              console.error("Error unregistering participant:", err);
            }
          });

          li.appendChild(span);
          li.appendChild(deleteBtn);
          participantsList.appendChild(li);
        });

        activityCard.appendChild(participantsList);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
