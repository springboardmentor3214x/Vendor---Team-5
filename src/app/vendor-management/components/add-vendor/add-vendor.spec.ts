import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddVendorComponent } from './add-vendor';

describe('AddVendor', () => {
  let component: AddVendorComponent;
  let fixture: ComponentFixture<AddVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddVendorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AddVendorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
