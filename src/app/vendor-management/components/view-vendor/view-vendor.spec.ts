import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewVendorComponent } from './view-vendor';

describe('ViewVendor', () => {
  let component: ViewVendorComponent;
  let fixture: ComponentFixture<ViewVendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewVendorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ViewVendorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
