import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Message {
  sender: string;
  subject: string;
  time: string;
  unread: number;
  content: string;
}

@Component({
  selector: 'app-communication',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './communication.html',
  styleUrls: ['./communication.css']
})
export class CommunicationComponent {

  messages: Message[] = [
    {
      sender: 'Procurement Manager',
      subject: 'Request for Additional Documents',
      time: '10:30 AM',
      unread: 1,
      content: 'Please provide the updated compliance certificates and insurance documents as per our latest requirements. You can upload the documents in your Vendor Profile section.'
    },
    {
      sender: 'Finance Officer',
      subject: 'Invoice 2026-204 Confirmation',
      time: 'Wednesday',
      unread: 2,
      content: 'Your submitted invoice has been received successfully and is currently under verification.'
    },
    {
      sender: 'Supply Chain Manager',
      subject: 'Delivery Schedule Update',
      time: 'Jul 08, 2026',
      unread: 0,
      content: 'The delivery schedule has been updated. Please review the revised shipment timeline.'
    },
    {
      sender: 'System Admin',
      subject: 'System Maintenance Notice',
      time: 'Jul 08, 2026',
      unread: 0,
      content: 'Vendor Portal will undergo scheduled maintenance this weekend from 10 PM to 1 AM.'
    },
    {
      sender: 'Procurement Manager',
      subject: 'New Order Assignment',
      time: 'Jul 08, 2026',
      unread: 0,
      content: 'A new purchase order has been assigned to your company. Please review it and respond as soon as possible.'
    }
  ];

  selectedMessage: Message = this.messages[0];

  selectMessage(message: Message): void {
    this.selectedMessage = message;
  }

}