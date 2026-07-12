import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditVendorComponent } from './edit-vendor';

describe('EditVendor', () => {
  let component: EditVendorComponent;
  let fixture: ComponentFixture<EditVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditVendorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EditVendorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
