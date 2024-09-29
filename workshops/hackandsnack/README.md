# Hack and Snack Workshop: Ethical Hacking Setup

   ## Introduction
   Welcome to the Cybersecurity Club's Hack and Snack Workshop! This guide will help you set up the necessary tools for our ethical hacking session. The goal is to introduce you to key concepts in ethical hacking and provide hands-on experience.

   Ethical hacking involves attempting to gain unauthorized access to systems with the intention of improving security. By practicing these skills, you'll develop an intuition for how systems work, how to troubleshoot errors, and how to navigate complex security landscapes.

   ## Prerequisites
   Before the workshop, please ensure you have the following software installed:
   - UTM (for Mac users)
   - Kali Linux UTM Image
   - Metasploitable 2

   ## Installation Steps

   ### 1. UTM Installation
   - For Mac users, especially those with M3 chips, we recommend using UTM.
   - Download UTM from: https://mac.getutm.app/
   - Follow the installation prompts to set up UTM on your Mac.

   ### 2. Kali Linux Setup
   - Download the Kali Linux UTM Image from: https://mac.getutm.app/gallery/kali-2023
   - In UTM, click on "Open" and select the downloaded Kali Linux file.
   - Click on "Settings" and allocate RAM and CPU cores as needed (more resources will result in faster performance).
   - Start the VM and log in with the default credentials:
     - Username: kali
     - Password: kali
   - Run the following commands to update the system:
     ```
     sudo apt update
     sudo apt upgrade
     ```
   - During setup, choose Latin 1 and Latin 5 for the console configuration.
   - Reboot the VM with: `sudo reboot now`

   ### 3. Metasploitable 2 Setup
   - Download Metasploitable 2 from: https://information.rapid7.com/download-metasploitable-2017.html
   - You may need to fill out a form with your information to download.
   - In UTM, create a new VM:
     - Choose "Other" for the operating system
     - Skip ISO Boot
     - Allocate 2024 MB of memory and 2 CPU cores
     - Set storage to 10 GB
     - Name the VM "Metasploitable2" or any name you prefer
   - In VM settings:
     - Under QEMU, uncheck "UEFI boot"
     - Under Drives, delete the existing drive
     - Import the Metasploitable 2 .vmdk file

   ## Troubleshooting Tips
   - If you encounter issues downloading Metasploitable 2, try using Safari instead of Chrome.
   - Ensure you have adequate disk space for both VMs.
   - If you experience performance issues, try allocating more resources to the VMs in UTM settings.

   We look forward to seeing you at the workshop! If you have any questions or issues with the setup, please don't hesitate to reach out to the club organizers.
