import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorProfileComponent } from './vendor-profile';

describe('VendorProfile', () => {
  let component: VendorProfileComponent;
  let fixture: ComponentFixture<VendorProfileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorProfileComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorProfileComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBe(true);
  });
});
