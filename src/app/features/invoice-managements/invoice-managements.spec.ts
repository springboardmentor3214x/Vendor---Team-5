import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvoiceManagements } from './invoice-managements';

describe('InvoiceManagements', () => {
  let component: InvoiceManagements;
  let fixture: ComponentFixture<InvoiceManagements>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InvoiceManagements],
    }).compileComponents();

    fixture = TestBed.createComponent(InvoiceManagements);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
