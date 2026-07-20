import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorAssignment } from './vendor-assignment';

describe('VendorAssignment', () => {
  let component: VendorAssignment;
  let fixture: ComponentFixture<VendorAssignment>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorAssignment],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorAssignment);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
